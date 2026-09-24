using Logic;
using Microsoft.AspNetCore.Mvc;

namespace API.Endpoints;

[ApiController]
public class ScoreboardDataController() : ControllerBase
{
    [HttpGet("internal/games")]
    public ActionResult GetGames()
    {
        return Ok(ScoreboardDataControllerLogic.GetGames());
    }
}