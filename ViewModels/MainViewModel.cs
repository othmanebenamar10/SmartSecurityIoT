<<<<<<< HEAD
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Threading.Tasks;

namespace SmartSecurityIoT.ViewModels
{
    public partial class MainViewModel : ObservableObject
    {
        [ObservableProperty]
        private string status = "System Ready";

        [RelayCommand]
        public async Task StartSystemAsync()
        {
            Status = "System running...";
            await Task.Delay(1000);
            Status = "All systems active";
        }
    }
}
=======

using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using SmartSecurityIoT.Services.Interfaces;

namespace SmartSecurityIoT.ViewModels;

public partial class MainViewModel : ObservableObject
{
    private readonly IVideoService _videoService;

    [ObservableProperty]
    private bool isTestMode;

    [ObservableProperty]
    private bool isRtspConnected;

    [ObservableProperty]
    private bool isPlcConnected;

    public MainViewModel(IVideoService videoService)
    {
        _videoService = videoService;
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
            }
            else
            {
                await _videoService.StopWebcamAsync();
                await _videoService.StartRtspAsync();
                IsTestMode = false;
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
        }
    }
}
>>>>>>> 1040ed1220214f4df9d7b4c004650f5c501a03e8
