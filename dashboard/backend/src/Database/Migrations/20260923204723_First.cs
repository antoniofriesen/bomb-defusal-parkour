using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace Database.Migrations
{
    /// <inheritdoc />
    public partial class First : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "Teams",
                columns: table => new
                {
                    TeamId = table.Column<int>(type: "INTEGER", nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    AnzahlMitglieder = table.Column<int>(type: "INTEGER", nullable: false),
                    TeamName = table.Column<string>(type: "TEXT", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Teams", x => x.TeamId);
                });

            migrationBuilder.CreateTable(
                name: "Games",
                columns: table => new
                {
                    SpielId = table.Column<int>(type: "INTEGER", nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    TeamId = table.Column<int>(type: "INTEGER", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Games", x => x.SpielId);
                    table.ForeignKey(
                        name: "FK_Games_Teams_TeamId",
                        column: x => x.TeamId,
                        principalTable: "Teams",
                        principalColumn: "TeamId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "GameData",
                columns: table => new
                {
                    StationDatenId = table.Column<int>(type: "INTEGER", nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    State = table.Column<string>(type: "TEXT", nullable: false),
                    Rating = table.Column<string>(type: "TEXT", nullable: false),
                    TimestampStart = table.Column<DateTime>(type: "TEXT", nullable: false),
                    TimestampEnd = table.Column<DateTime>(type: "TEXT", nullable: true),
                    StationId = table.Column<int>(type: "INTEGER", nullable: false),
                    SpielId = table.Column<int>(type: "INTEGER", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_GameData", x => x.StationDatenId);
                    table.ForeignKey(
                        name: "FK_GameData_Games_SpielId",
                        column: x => x.SpielId,
                        principalTable: "Games",
                        principalColumn: "SpielId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_GameData_SpielId",
                table: "GameData",
                column: "SpielId");

            migrationBuilder.CreateIndex(
                name: "IX_Games_TeamId",
                table: "Games",
                column: "TeamId",
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "GameData");

            migrationBuilder.DropTable(
                name: "Games");

            migrationBuilder.DropTable(
                name: "Teams");
        }
    }
}
