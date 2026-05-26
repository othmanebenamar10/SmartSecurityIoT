using Serilog;
using SmartSecurityIoT.Services.Interfaces;
using Sharp7;

namespace SmartSecurityIoT.Services;

public class PlcService : IPlcService
{
    private readonly S7Client _client = new();
    private readonly ILogger _logger = Log.ForContext<PlcService>();

    public async Task ConnectAsync()
    {
        if (_client.Connected) return;

        await Task.Run(() =>
        {
            var plcIp = Security.SecureConfig.PlcIp;
            _logger.Information("Connecting to PLC at {PlcIp}...", plcIp);

            int result = _client.ConnectTo(plcIp, 0, 1);
            if (result != 0)
                throw new InvalidOperationException(
                    $"PLC Connection failed: {_client.ErrorText(result)}");

            _logger.Information("PLC connected successfully");
        });
    }

    public async Task TriggerLightAsync(int durationSeconds)
    {
        await ConnectAsync();

        _logger.Information("Triggering light for {Duration}s", durationSeconds);
        byte[] buffer = { 0x01 };
        await Task.Run(() => _client.DBWrite(1, 0, 1, buffer));

        await Task.Delay(durationSeconds * 1000);

        buffer[0] = 0x00;
        await Task.Run(() => _client.DBWrite(1, 0, 1, buffer));
        _logger.Information("Light turned off");
    }
}
