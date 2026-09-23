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

    [HttpPost("dashboard/backend/insertbullshit")]
    public ActionResult AddMockData()
    {
        var result = Logic.GameControllerLogic.StoreStationData(new Logic.Models.StationDatenCreateModel(68, "status oder so", "echt toll", DateTime.Now, null));

        if (result == null)
        {
            return BadRequest();
        }

        return Ok(result);
    }
}