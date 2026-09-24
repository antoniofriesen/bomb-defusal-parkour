namespace Logic.Models;
public record StationDatenCreateModel(
    int StationId,
    string State,
    string? Rating,
    DateTime? TimestampStart,
    DateTime? TimestampEnd
);