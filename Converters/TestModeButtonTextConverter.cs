using System.Globalization;
using System.Windows.Data;

namespace SmartSecurityIoT.Converters;

public class TestModeButtonTextConverter : IValueConverter
{
    public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is bool isTestMode && isTestMode)
            return "Arrêter Test";

        return "Mode Test (Webcam)";
    }

    public object ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        throw new NotSupportedException();
    }
}
