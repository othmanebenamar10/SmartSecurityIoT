
namespace SmartSecurityIoT.Services.Interfaces;

public interface IVideoService
{
    Task StartRtspAsync();
    Task StopRtspAsync();
    Task StartWebcamAsync(int cameraIndex);
    Task StopWebcamAsync();
}
