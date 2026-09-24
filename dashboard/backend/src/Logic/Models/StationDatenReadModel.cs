namespace Logic.Models;
public record StationDatenReadModel(
    int StationDatenId,
    int StationId,
    int SpielId,
    string State,
    string? Rating,
    DateTime? TimestampStart,
    DateTime? TimestampEnd
);