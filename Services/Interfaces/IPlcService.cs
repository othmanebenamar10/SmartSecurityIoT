<<<<<<< HEAD
using System.Threading.Tasks;

namespace SmartSecurityIoT.Services.Interfaces
{
    public interface IPlcService
    {
        Task ConnectAsync();
        Task WriteAsync(string address, int value);
    }
}
=======

namespace SmartSecurityIoT.Services.Interfaces;

public interface IPlcService
{
    Task ConnectAsync();
    Task TriggerLightAsync(int durationSeconds);
}
>>>>>>> 1040ed1220214f4df9d7b4c004650f5c501a03e8
