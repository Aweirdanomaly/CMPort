let errorIDs={"1":"underC", "2": "overD"}
$(document).ready(function () {
  //alert("beginning")

  $(btn).click(function () {
    $("#loading").show()
    
        $.ajax({
        type: "POST",
        url: "test",
          data: { "tickers": document.getElementById("tickers").value, "days": document.getElementById("days").value },
          datatype: "application/json",
          success: function (data) {
            data = JSON.parse(data)

            keys = Object.keys(data)
            console.log(keys)
            if (data["corr"]===undefined) {
              for (let x in keys) {
                //console.log(errorIDs[keys[x]]+$("#"+errorIDs[keys[x]]))
                document.getElementById(errorIDs[keys[x]]).style.display = "inline"
              }
              $("#loading").hide()
              $("#stats").hide()
            }
            else {
              //document.getElementById("underC").hide()
              $("#err>p").each((id, elem) => {
                elem.style.display="none";
                console.log(elem);
              })

              //document.getElementById("laters").innerHTML = data
              $("#stats div").each((index, elem) => {
                elem.innerHTML = (data[elem.id])
              })

              $(data["fig"]).appendTo(document.getElementById("fig"))
              //$(data["fig"]).attr("id", "fig").replace(document.getElementById("fig"))

              $("#loading").hide()
              $("#stats").show()
            }
        },
        error: function(jqXHR, textStatus, errorThrown) { 
          console.log(errorThrown)

          $("#loading").hide()
        }
      })
        
    })
})    
