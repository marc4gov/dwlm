// Dgraph returns an array of objects
@json
class GetPumpingStationResponse {
  station: Array<PumpingStation> = []
}

export function getPumpingStation2(xid: string): PumpingStation | null {
    const statement = `
    query pumpingStation2($xid: string!) {
      station(func: eq(xid, $xid)) {
        id: uid
        xid
        name
        profiles {
          id: uid
          datestring
          flow_per_hour {
            id: uid
            h0
            h1
            h2
            h3
            h4
            h5
            h6
            h7
            h8
            h9
            h10
            h11
            h12
            h13
            h14
            h15
            h16
            h17
            h18
            h19
            h20
            h21
            h22
            h23
          }
          price_per_hour {
            id: uid
            h0
            h1
            h2
            h3
            h4
            h5
            h6
            h7
            h8
            h9
            h10
            h11
            h12
            h13
            h14
            h15
            h16
            h17
            h18
            h19
            h20
            h21
            h22
            h23
          }
          action_per_hour {
            id: uid
            h0
            h1
            h2
            h3
            h4
            h5
            h6
            h7
            h8
            h9
            h10
            h11
            h12
            h13
            h14
            h15
            h16
            h17
            h18
            h19
            h20
            h21
            h22
            h23
          }
        }
      }
    }`
  
  

  const vars = new dgraph.Variables()
  vars.set("$xid", xid)

  const resp = dgraph.execute(
    DGRAPH_CONNECTION,
    new dgraph.Request(new dgraph.Query(statement, vars)),
  )
  
  // Then parse the pumpingStation2 string which contains the actual data
  const pumpingstations = JSON.parse<GetPumpingStationResponse>(resp.Json).station
  
  // Return the first station that matches
  return pumpingstations[0]
  // return resp.Json
}