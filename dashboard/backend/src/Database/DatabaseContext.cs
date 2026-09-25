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
    }

    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    {
        if (!optionsBuilder.IsConfigured)
        {
            var connStr = Environment.GetEnvironmentVariable("DATABASE_CONNECTION_STRING") ?? "Data Source=Backend.db";
            optionsBuilder.UseSqlite(connStr);
        }
    }
}
