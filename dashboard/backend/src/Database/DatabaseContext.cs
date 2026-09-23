using Database.Entities;
using Microsoft.EntityFrameworkCore;

namespace Database;

public class DatabaseContext : DbContext
{
    public DbSet<Spiel> Games => Set<Spiel>();
    public DbSet<Team> Teams => Set<Team>();
    public DbSet<StationDaten> GameData => Set<StationDaten>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        modelBuilder.Entity<Spiel>().HasMany(s => s.StationDaten).WithOne(d => d.Spiel).HasForeignKey(d => d.SpielId).OnDelete(DeleteBehavior.Cascade);
        //modelBuilder.Entity<Team>().HasOne(t => t.Spiel).WithOne(s => s.Team).HasForeignKey(s => s.);
    }

    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    {
        if (!optionsBuilder.IsConfigured)
        {
            optionsBuilder.UseSqlite("Data Source=Backend.db");
        }
    }
}
