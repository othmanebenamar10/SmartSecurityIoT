using System.Threading.Tasks;
using SmartSecurityIoT.Services.Interfaces;
using Sharp7;

namespace SmartSecurityIoT.Services
{
    public class PlcService : IPlcService
    {
        private readonly S7Client _client = new();

        public async Task ConnectAsync()
        {
            if (_client.Connected) return;
            
            await Task.Run(() => 
            {
                int result = _client.ConnectTo(Security.SecureConfig.PlcIp, 0, 1);
                if (result != 0) throw new System.Exception($"PLC Connection failed: {_client.ErrorText(result)}");
            });
        }

        public async Task TriggerLightAsync(int durationSeconds)
        {
            await ConnectAsync();
            // Exemple : Mise à 1 du bit 0.0 dans le DB1
            byte[] buffer = { 0x01 };
            await Task.Run(() => _client.DBWrite(1, 0, 1, buffer));
        }
    }
}