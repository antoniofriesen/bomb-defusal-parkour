using Microsoft.AspNetCore.Http.HttpResults;
using Microsoft.AspNetCore.Mvc;

namespace API.Endpoints;

[ApiController]
public class GameController() : ControllerBase
{
    [HttpPost("dashboard/backend/start")]
    public ActionResult StartGame([FromBody] StartGameRequest request)
    {
        string code = Logic.GameControllerLogic.StartGame(request.team_name, request.member_count);
        return Ok("{ \"code\": \"" + code + "\" }");
    }

    [HttpPost("dashboard/backend/stop")]
    public ActionResult StopGame([FromBody] string outcome)
    {
        Logic.GameControllerLogic.StopGame(outcome);
        return Ok();
    }

    [HttpGet("dashboard/backend/status")]
    public ActionResult GetGameStatus()
    {
        var result = Logic.GameControllerLogic.GetGameStatus();
        if (result == null)
        {
            return BadRequest();
        }

        return Ok(result);
    }
}

public record StartGameRequest(string team_name, int member_count);