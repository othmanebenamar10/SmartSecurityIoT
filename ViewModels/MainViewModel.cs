
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
