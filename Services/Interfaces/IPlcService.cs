
namespace SmartSecurityIoT.Services.Interfaces;

public interface IPlcService
{
    Task ConnectAsync();
    Task TriggerLightAsync(int durationSeconds);
}
