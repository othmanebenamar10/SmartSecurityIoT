<<<<<<< HEAD
using System.Threading.Tasks;
=======

>>>>>>> 1040ed1220214f4df9d7b4c004650f5c501a03e8
namespace SmartSecurityIoT.Security;

public static class SecureConfig
{
<<<<<<< HEAD
    private static string GetOrThrow(string key) =>
        Environment.GetEnvironmentVariable(key) 
        ?? throw new InvalidOperationException($"Critical configuration missing: {key}. Please set this environment variable.");

    public static string TelegramToken =>
        GetOrThrow("TELEGRAM_BOT_TOKEN");

    public static string PlcIp =>
        GetOrThrow("PLC_IP");

    public static string RtspUrl =>
        GetOrThrow("RTSP_URL");

    public static string DatabasePassword => 
        GetOrThrow("DB_ENCRYPTION_KEY");
=======
    public static string TelegramToken =>
        Environment.GetEnvironmentVariable("TELEGRAM_BOT_TOKEN")
        ?? throw new Exception("Missing TELEGRAM_BOT_TOKEN");

    public static string PlcIp =>
        Environment.GetEnvironmentVariable("PLC_IP")
        ?? throw new Exception("Missing PLC_IP");

    public static string RtspUrl =>
        Environment.GetEnvironmentVariable("RTSP_URL")
        ?? throw new Exception("Missing RTSP_URL");
>>>>>>> 1040ed1220214f4df9d7b4c004650f5c501a03e8
}
