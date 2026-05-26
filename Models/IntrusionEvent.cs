namespace SmartSecurityIoT.Models;

public class IntrusionEvent
{
    public int Id { get; set; }
    public byte[] Snapshot { get; set; } = Array.Empty<byte>();
    public DateTime EventDate { get; set; } = DateTime.UtcNow;
    public bool LivenessPassed { get; set; }
}
