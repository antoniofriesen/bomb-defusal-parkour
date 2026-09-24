namespace Database.Entities;

public class StationDaten
{
    public int StationDatenId {get; set;}
    public string State {get; set;} = null!;
    public string? Rating {get; set;} = null!;
    public DateTime? TimestampStart {get; set;} = null!;
    public DateTime? TimestampEnd {get; set;} = null!;
    public int StationId {get; set;}
    public int SpielId {get; set;}
    public Spiel Spiel {get; set;} = null!;
}