/**
 * Helper functions for products classes.
 */
import { JSON } from "json-as"
import { PumpingStation, EnergyProfile, Project, Category } from "./classes"
import { injectNodeUid, GraphSchema } from "./dgraph-utils"

const project_schema: GraphSchema = new GraphSchema()
const pumpingstation_schema: GraphSchema = new GraphSchema()
const energyprofile_schema: GraphSchema = new GraphSchema()
const budget_schema: GraphSchema = new GraphSchema()

project_schema.node_types.set("Project", {
  id_field: "Project.id",
  relationships: [
    { predicate: "Project.category", type: "Category" },
    { predicate: "Project.budgets", type: "Budget[]" },
    // { predicate: "Project.pumpingstation", type: "PumpingStation" },
  ],
})

project_schema.node_types.set("Category", {
  id_field: "Category.id",
  relationships: [],
})

project_schema.node_types.set("Budget", {
  id_field: "Budget.id",
  relationships: [],
})


// Add PumpingStation node type to pumpingstation_schema
pumpingstation_schema.node_types.set("PumpingStation", {
  id_field: "PumpingStation.id",
  relationships: [
    { predicate: "PumpingStation.energyprofiles", type: "EnergyProfile[]" }
  ],
});

// Add EnergyProfile node type to pumpingstation_schema
pumpingstation_schema.node_types.set("EnergyProfile", {
  id_field: "EnergyProfile.id",
  relationships: [],
});


energyprofile_schema.node_types.set("EnergyProfile", {
  id_field: "EnergyProfile.id",
  relationships: [
    { predicate: "EnergyProfile.pumpingstation", type: "PumpingStation" },
  ],
})

energyprofile_schema.node_types.set("EnergyProfile", {
  id_field: "PumpingStation.id",
  relationships: [
  ],
})

export function buildPumpingStationMutationJson(connection: string, pumpingstation: PumpingStation): string {
  var payload = JSON.stringify(pumpingstation)

  payload = injectNodeUid(connection, payload, "PumpingStation", pumpingstation_schema)

  return payload
}

export function buildEnergyProfileMutationJson(connection: string, energyprofile: EnergyProfile): string {
  var payload = JSON.stringify(energyprofile)

  payload = injectNodeUid(connection, payload, "EnergyProfile", energyprofile_schema)

  return payload
}

export function buildProjectMutationJson(connection: string, project: Project): string {
  var payload = JSON.stringify(project)

  payload = injectNodeUid(connection, payload, "Project", project_schema)

  return payload
}