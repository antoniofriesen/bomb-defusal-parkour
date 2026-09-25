using Microsoft.EntityFrameworkCore;

namespace Database.Entities;

public class Team
{
    public int TeamId {get; set;}
    public int AnzahlMitglieder {get; set;}
    public string TeamName {get; set;} = null!;
    public Spiel Spiel {get; set;} = null!;
}