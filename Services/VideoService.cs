using OpenCvSharp;
using Serilog;
using SmartSecurityIoT.Services.Interfaces;

namespace SmartSecurityIoT.Services;

public class VideoService : IVideoService, IDisposable
{
    private VideoCapture? _capture;
    private CancellationTokenSource? _cts;
    private readonly ILogger _logger = Log.ForContext<VideoService>();

    public bool IsStreaming { get; private set; }
    public event Action<byte[]>? FrameReceived;

    public async Task StartRtspAsync()
    {
        if (IsStreaming) return;

        var rtspUrl = Security.SecureConfig.RtspUrl;
        _logger.Information("Starting RTSP stream from {Url}", rtspUrl);

        await Task.Run(() =>
        {
            _capture = new VideoCapture(rtspUrl);
            if (!_capture.IsOpened())
                throw new InvalidOperationException($"Cannot open RTSP stream: {rtspUrl}");
        });

        IsStreaming = true;
        StartFrameLoop();
        _logger.Information("RTSP stream started");
    }

    public Task StopRtspAsync()
    {
        StopCapture();
        _logger.Information("RTSP stream stopped");
        return Task.CompletedTask;
    }

    public async Task StartWebcamAsync(int cameraIndex)
    {
        if (IsStreaming) return;

        _logger.Information("Starting webcam (index: {Index})", cameraIndex);

        await Task.Run(() =>
        {
            _capture = new VideoCapture(cameraIndex);
            if (!_capture.IsOpened())
                throw new InvalidOperationException($"Cannot open webcam at index {cameraIndex}");
        });

        IsStreaming = true;
        StartFrameLoop();
        _logger.Information("Webcam started");
    }

    public Task StopWebcamAsync()
    {
        StopCapture();
        _logger.Information("Webcam stopped");
        return Task.CompletedTask;
    }

    public async Task<byte[]?> CaptureFrameAsync()
    {
        if (_capture == null || !_capture.IsOpened())
            return null;

        return await Task.Run(() =>
        {
            using var frame = new Mat();
            if (!_capture.Read(frame) || frame.Empty())
                return null;

            Cv2.ImEncode(".jpg", frame, out var buffer);
            return buffer;
        });
    }

    private void StartFrameLoop()
    {
        _cts = new CancellationTokenSource();
        var token = _cts.Token;

        Task.Run(async () =>
        {
            using var frame = new Mat();

            while (!token.IsCancellationRequested && _capture != null && _capture.IsOpened())
            {
                if (_capture.Read(frame) && !frame.Empty())
                {
                    Cv2.ImEncode(".jpg", frame, out var buffer);
                    FrameReceived?.Invoke(buffer);
                }

                await Task.Delay(33, token);
            }
        }, token);
    }

    private void StopCapture()
    {
        _cts?.Cancel();
        _cts?.Dispose();
        _cts = null;

        _capture?.Release();
        _capture?.Dispose();
        _capture = null;

        IsStreaming = false;
    }

    public void Dispose()
    {
        StopCapture();
        GC.SuppressFinalize(this);
    }
}
