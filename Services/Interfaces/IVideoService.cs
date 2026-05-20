<<<<<<< HEAD
using System.Threading.Tasks;

namespace SmartSecurityIoT.Services.Interfaces
{
    public interface IVideoService
    {
        Task StartCameraAsync();
        Task StopCameraAsync();
        Task<byte[]> CaptureFrameAsync();
    }
}
=======

namespace SmartSecurityIoT.Services.Interfaces;

public interface IVideoService
{
    Task StartRtspAsync();
    Task StopRtspAsync();
    Task StartWebcamAsync(int cameraIndex);
    Task StopWebcamAsync();
}
>>>>>>> 1040ed1220214f4df9d7b4c004650f5c501a03e8
