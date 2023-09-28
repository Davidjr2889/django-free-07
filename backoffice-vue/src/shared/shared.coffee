# eslint-disable-next-line
export responseUnwrap = (res) ->
  if res.hasOwnProperty("msg") and res.msg != ""
    { success: false, msg: res.msg }
  else
    { success: true }


export handleNetworkExceptionShowErrors = (e) ->
  if e.hasOwnProperty("status") and e.status != 200
    try
      message = JSON.parse(e.message)
      if message.hasOwnProperty("error")
        kendo.alert(message.error)
      else
        kendo.alert(message)
    catch
      kendo.alert("Problemas com o servidor!")
      # kendo.alert("Problemas com o servidor: #{e.message}")
  else
    try
      message = JSON.parse(e.message)
      if message.hasOwnProperty("error")
        kendo.alert(message.error)
      else
        kendo.alert(message)
    catch error
      kendo.alert("Ocorreu um problema com a aplicação.")
