using Microsoft.AspNetCore.Mvc;

namespace API.Endpoints;

[ApiController]
public class GameController() : ControllerBase
{
    [HttpGet("dashboard/backend/ping")]
    public ActionResult PingPong()
    {
        return Ok("Pong!");
    }
}