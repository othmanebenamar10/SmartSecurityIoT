using Serilog;

namespace SmartSecurityIoT.Security;

public static class SecureConfig
{
    private static string GetOrThrow(string key) =>
        Environment.GetEnvironmentVariable(key)
        ?? throw new InvalidOperationException(
            $"Critical configuration missing: {key}. Please set this environment variable.");

    private static string GetOrDefault(string key, string defaultValue = "")
    {
        var value = Environment.GetEnvironmentVariable(key);
        if (string.IsNullOrEmpty(value))
        {
            Log.Warning("Configuration {Key} not set, using default", key);
            return defaultValue;
        }
        return value;
    }

    public static string TelegramToken =>
        GetOrDefault("TELEGRAM_BOT_TOKEN");

    public static string TelegramChatId =>
        GetOrDefault("TELEGRAM_CHAT_ID");

    public static string PlcIp =>
        GetOrDefault("PLC_IP", "192.168.0.1");

    public static string RtspUrl =>
        GetOrDefault("RTSP_URL", "rtsp://localhost:554/stream");

    public static string DatabasePassword =>
        GetOrDefault("DB_ENCRYPTION_KEY", "SmartSecurityDev2024");

    public static bool IsConfigured(string key) =>
        !string.IsNullOrEmpty(Environment.GetEnvironmentVariable(key));
}
