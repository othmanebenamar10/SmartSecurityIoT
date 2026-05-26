namespace SmartSecurityIoT.Services.Interfaces;

public interface IVideoService
{
    Task StartRtspAsync();
    Task StopRtspAsync();
    Task StartWebcamAsync(int cameraIndex);
    Task StopWebcamAsync();
    Task<byte[]?> CaptureFrameAsync();
    bool IsStreaming { get; }
    event Action<byte[]>? FrameReceived;
}
