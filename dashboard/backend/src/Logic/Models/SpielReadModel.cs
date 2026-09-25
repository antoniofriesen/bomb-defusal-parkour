namespace Logic.Models;
public record SpielReadModel(
    int GameId,
    string Outcome,
    string TeamName,
    DateTime StartedAt,
    DateTime? EndedAt
);