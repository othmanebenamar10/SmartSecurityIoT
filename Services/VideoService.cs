using System.Threading.Tasks;
using SmartSecurityIoT.Services.Interfaces;

namespace SmartSecurityIoT.Services
{
    public class VideoService : IVideoService
    {
        public Task StartRtspAsync() => Task.CompletedTask;
        public Task StopRtspAsync() => Task.CompletedTask;
        public Task StartWebcamAsync(int cameraIndex) => Task.CompletedTask;
        public Task StopWebcamAsync() => Task.CompletedTask;
    }
}