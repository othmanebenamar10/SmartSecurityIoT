using System.Collections.ObjectModel;
using System.IO;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Serilog;
using SmartSecurityIoT.Models;
using SmartSecurityIoT.Services.Interfaces;

namespace SmartSecurityIoT.ViewModels;

public partial class MainViewModel : ObservableObject, IDisposable
{
    private readonly IVideoService _videoService;
    private readonly IBiometricService _biometricService;
    private readonly INotificationService _notificationService;
    private readonly IDatabaseService _databaseService;
    private readonly IPlcService _plcService;
    private readonly ILogger _logger = Log.ForContext<MainViewModel>();

    [ObservableProperty]
    private bool isTestMode;

    [ObservableProperty]
    private bool isRtspConnected;

    [ObservableProperty]
    private bool isPlcConnected;

    [ObservableProperty]
    private string status = "Système prêt";

    [ObservableProperty]
    private ImageSource? currentFrame;

    [ObservableProperty]
    private string rtspStatusText = "RTSP DÉCONNECTÉ";

    [ObservableProperty]
    private string plcStatusText = "PLC DÉCONNECTÉ";

    [ObservableProperty]
    private Brush rtspStatusColor = Brushes.Red;

    [ObservableProperty]
    private Brush plcStatusColor = Brushes.Red;

    public ObservableCollection<DetectionEntry> DetectionHistory { get; } = new();

    public MainViewModel(
        IVideoService videoService,
        IBiometricService biometricService,
        INotificationService notificationService,
        IDatabaseService databaseService,
        IPlcService plcService)
    {
        _videoService = videoService;
        _biometricService = biometricService;
        _notificationService = notificationService;
        _databaseService = databaseService;
        _plcService = plcService;

        _videoService.FrameReceived += OnFrameReceived;
    }

    private void OnFrameReceived(byte[] frameData)
    {
        System.Windows.Application.Current?.Dispatcher.Invoke(() =>
        {
            var image = new BitmapImage();
            using var stream = new MemoryStream(frameData);
            image.BeginInit();
            image.CacheOption = BitmapCacheOption.OnLoad;
            image.StreamSource = stream;
            image.EndInit();
            image.Freeze();
            CurrentFrame = image;
        });
    }

    [RelayCommand]
    public async Task ConnectRtspAsync()
    {
        try
        {
            Status = "Connexion RTSP...";
            await _videoService.StartRtspAsync();
            IsRtspConnected = true;
            RtspStatusText = "RTSP CONNECTÉ";
            RtspStatusColor = Brushes.LimeGreen;
            Status = "Flux RTSP actif";
        }
        catch (Exception ex)
        {
            _logger.Error(ex, "RTSP connection failed");
            Status = $"Erreur RTSP: {ex.Message}";
            RtspStatusText = "RTSP ERREUR";
            RtspStatusColor = Brushes.Red;
        }
    }

    [RelayCommand]
    public async Task ConnectPlcAsync()
    {
        try
        {
            Status = "Connexion PLC...";
            await _plcService.ConnectAsync();
            IsPlcConnected = true;
            PlcStatusText = "PLC CONNECTÉ";
            PlcStatusColor = Brushes.LimeGreen;
            Status = "PLC connecté";
        }
        catch (Exception ex)
        {
            _logger.Error(ex, "PLC connection failed");
            Status = $"Erreur PLC: {ex.Message}";
            PlcStatusText = "PLC ERREUR";
            PlcStatusColor = Brushes.Red;
        }
    }

    [RelayCommand]
    public async Task ToggleTestMode()
    {
        try
        {
            if (!IsTestMode)
            {
                await _videoService.StopRtspAsync();
                await _videoService.StartWebcamAsync(0);
                IsTestMode = true;
                IsRtspConnected = false;
                RtspStatusText = "MODE TEST";
                RtspStatusColor = Brushes.Orange;
                Status = "Mode test: Webcam active";
            }
            else
            {
                await _videoService.StopWebcamAsync();
                IsTestMode = false;
                RtspStatusText = "RTSP DÉCONNECTÉ";
                RtspStatusColor = Brushes.Red;
                Status = "Mode test désactivé";
            }
        }
        catch (Exception ex)
        {
            _logger.Error(ex, "Toggle test mode failed");
            Status = $"Erreur: {ex.Message}";
        }
    }

    [RelayCommand]
    public async Task RecognizeFaceAsync()
    {
        try
        {
            Status = "Reconnaissance en cours...";

            var frame = await _videoService.CaptureFrameAsync();
            if (frame == null)
            {
                Status = "Aucune image capturée";
                return;
            }

            var livenessOk = await _biometricService.DetectLivenessAsync(frame);
            if (!livenessOk)
            {
                Status = "Liveness check échoué — possible spoofing";
                await LogIntrusion(frame, false);
                return;
            }

            var embedding = await _biometricService.GenerateEmbeddingAsync(frame);
            var users = await _databaseService.GetAllUsersAsync();

            foreach (var user in users)
            {
                var storedEmbedding = ConvertBlobToFloatArray(user.Embedding);
                var distance = _biometricService.CalculateDistance(embedding, storedEmbedding);

                if (_biometricService.ValidateThreshold(distance))
                {
                    Status = $"Accès autorisé: {user.FullName}";
                    AddDetection(user.FullName, true);
                    _logger.Information("Access granted to {User}", user.FullName);
                    return;
                }
            }

            Status = "Visage inconnu détecté";
            AddDetection("Visage inconnu", false);
            await LogIntrusion(frame, true);
            await _notificationService.SendTelegramAlertAsync(
                "⚠️ Visage inconnu détecté à l'entrée", "");
        }
        catch (Exception ex)
        {
            _logger.Error(ex, "Face recognition failed");
            Status = $"Erreur reconnaissance: {ex.Message}";
        }
    }

    private async Task LogIntrusion(byte[] snapshot, bool livenessPassed)
    {
        var intrusion = new IntrusionEvent
        {
            Snapshot = snapshot,
            EventDate = DateTime.UtcNow,
            LivenessPassed = livenessPassed
        };
        await _databaseService.LogIntrusionEventAsync(intrusion);
    }

    private void AddDetection(string name, bool authorized)
    {
        System.Windows.Application.Current?.Dispatcher.Invoke(() =>
        {
            DetectionHistory.Insert(0, new DetectionEntry
            {
                Name = name,
                Time = DateTime.Now.ToString("dd/MM/yyyy HH:mm"),
                IsAuthorized = authorized
            });

            while (DetectionHistory.Count > 50)
                DetectionHistory.RemoveAt(DetectionHistory.Count - 1);
        });
    }

    private static float[] ConvertBlobToFloatArray(byte[] blob)
    {
        var floats = new float[blob.Length / sizeof(float)];
        Buffer.BlockCopy(blob, 0, floats, 0, blob.Length);
        return floats;
    }

    public void Dispose()
    {
        _videoService.FrameReceived -= OnFrameReceived;
        GC.SuppressFinalize(this);
    }
}

public class DetectionEntry
{
    public string Name { get; set; } = string.Empty;
    public string Time { get; set; } = string.Empty;
    public bool IsAuthorized { get; set; }
    public Brush StatusColor => IsAuthorized ? Brushes.LimeGreen : Brushes.Orange;
}
