
namespace SmartSecurityIoT.Security;

public static class SecureConfig
{
    public static string TelegramToken =>
        Environment.GetEnvironmentVariable("TELEGRAM_BOT_TOKEN")
        ?? throw new Exception("Missing TELEGRAM_BOT_TOKEN");

    public static string PlcIp =>
        Environment.GetEnvironmentVariable("PLC_IP")
        ?? throw new Exception("Missing PLC_IP");

    public static string RtspUrl =>
        Environment.GetEnvironmentVariable("RTSP_URL")
        ?? throw new Exception("Missing RTSP_URL");
}
