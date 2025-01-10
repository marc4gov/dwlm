/**
 * Helper functions for products classes.
 */
import { JSON } from "json-as"
import { PumpingStation } from "./classes"
import { injectNodeUid, GraphSchema } from "./dgraph-utils"

const pumpingstation_schema: GraphSchema = new GraphSchema()


// Add PumpingStation node type to pumpingstation_schema
pumpingstation_schema.node_types.set("PumpingStation", {
  id_field: "PumpingStation.id",
  relationships: [
  ],
});


export function buildPumpingStationMutationJson(connection: string, pumpingstation: PumpingStation): string {
  var payload = JSON.stringify(pumpingstation)

  payload = injectNodeUid(connection, payload, "PumpingStation", pumpingstation_schema)

  return payload
}
