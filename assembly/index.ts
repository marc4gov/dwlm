import { postgresql } from "@hypermode/modus-sdk-as"

// the name of the PostgreSQL connection, as specified in the modus.json manifest
const connection = "postgresql"

@json
class Person {
  name!: string
  age!: i32
}

export function getPerson(name: string): Person {
  const query = "select * from persons where name = $1"

  const params = new postgresql.Params()
  params.push(name)

  const response = postgresql.query<Person>(connection, query, params)
  return response.rows[0]
}

import { models } from "@hypermode/modus-sdk-as"

import {
  AnthropicMessagesInput,
  AnthropicMessagesModel,
  AnthropicMessagesOutput,
  UserMessage,
  AssistantMessage
  ,
} from "@hypermode/modus-sdk-as/models/anthropic/messages"

// this model name should match the one defined in the modus.json manifest file
const modelName: string = "text-generator"

export function generateText(prompt: string): string {
  const model = models.getModel<AnthropicMessagesModel>(modelName)
  const input = model.createInput([
    new AssistantMessage("you are a helpful assistant"),
    new UserMessage(prompt)
  ])

  // this is one of many optional parameters available for the OpenAI chat interface
  input.temperature = 0.7

  const output = model.invoke(input)
  let text = output.content[0].text
  if (text == null) {
    text = ""
  }
  return text
}

import { EmbeddingsModel } from "@hypermode/modus-sdk-as/models/experimental/embeddings"

export function embed(texts: string[]): f32[][] {
  // "minilm" is the model name declared in the application manifest
  const model = models.getModel<EmbeddingsModel>("minilm")
  const input = model.createInput(texts)
  const output = model.invoke(input)
  return output.predictions
}


import { collections } from "@hypermode/modus-sdk-as"

export function addProduct(description: string): string {
  const response = collections.upsert(
    "myProducts", // Collection name defined in the manifest
    null, // using null to let Modus generate a unique ID
    description, // the text to store
    // no labels for this item
    // no namespace provided, use defautl namespace
  )
  return response.keys[0] // return the identifier of the item
}

export function searchProducts2(
  product_description: string,
  maxItems: i32,
): collections.CollectionSearchResult {
  const response = collections.search(
    "myProducts", // collection name declared in the application manifest
    "searchMethod1", // search method declared for this collection in the manifest
    product_description, // text to search for
    maxItems,
    true, //  returnText: bool, true to return the items text.
    // no namespace provide, use the default namespace
  )
  return response
}

export function searchSimilarProducts(
  productId: string,
  maxItems: i32,
): collections.CollectionSearchResult {
  const embedding_vector = collections.getVector(
    "myProducts", // Collection name defined in the manifest
    "searchMethod1", // search method declared for the collection
    productId, // key of the collection item to retrieve
  )
  // search for similar products using the embedding vector
  const response = collections.searchByVector(
    "myProducts",
    "searchMethod1",
    embedding_vector,
    maxItems,
    true, // get the product description
  )

  return response
}


import { dgraph } from "@hypermode/modus-sdk-as"
import { PumpingStation, EnergyProfile, Project} from "./classes"
import { embedText } from "./embeddings"
import { buildPumpingStationMutationJson, buildEnergyProfileMutationJson, buildProjectMutationJson} from "./pumpingstation-helpers"
import {
  deleteNodePredicates,
  ListOf,
  searchBySimilarity,
  getEntityById,
  addEmbeddingToJson,
} from "./dgraph-utils"

const DGRAPH_CONNECTION = "dgraph"

/**
 * Add or update a new product to the database
 */

export function upsertPumpingStation(pumpingstation: PumpingStation): Map<string, string> | null {

  
  var payload = buildPumpingStationMutationJson(DGRAPH_CONNECTION, pumpingstation)
  const embedding = embedText([pumpingstation.name])[0]
  payload = addEmbeddingToJson(payload, "PumpingStation.embedding", embedding)

  const mutations: dgraph.Mutation[] = [new dgraph.Mutation(payload)]
  const uids = dgraph.execute(DGRAPH_CONNECTION, new dgraph.Request(null, mutations)).Uids

  return uids
}

export function upsertEnergyProfile(energyprofile: EnergyProfile): Map<string, string> | null {
  var payload = buildEnergyProfileMutationJson(DGRAPH_CONNECTION, energyprofile)

  // const embedding = embedText([energyprofile.day.toString(), energyprofile.month.toString()])[0]
  // payload = addEmbeddingToJson(payload, "EnergyProfile.embedding", embedding)

  const mutations: dgraph.Mutation[] = [new dgraph.Mutation(payload)]
  const uids = dgraph.execute(DGRAPH_CONNECTION, new dgraph.Request(null, mutations)).Uids

  return uids
}

export function upsertProject(project: Project): Map<string, string> | null {
  var payload = buildProjectMutationJson(DGRAPH_CONNECTION, project)

  const mutations: dgraph.Mutation[] = [new dgraph.Mutation(payload)]
  const uids = dgraph.execute(DGRAPH_CONNECTION, new dgraph.Request(null, mutations)).Uids

  return uids
}

// Dgraph returns an array of objects
@json
class getPumpingStationResponse {
  pumpingstations: PumpingStation[] = []
}

// export function getPumpingStation2(name: string): PumpingStation {
//   const statement = `  
//   query getPumpingStation($name: string) {
//     pumpingstations(func: eq(name, $name))  {
//         name
//         id
//     }
//   }`

//   const vars = new dgraph.Variables()
//   vars.set("$name", name)

//   const resp = dgraph.execute(
//     DGRAPH_CONNECTION,
//     new dgraph.Request(new dgraph.Query(statement, vars)),
//   )
//   const pumpingstations = JSON.parse<getPumpingStationResponse>(resp.Json).pumpingstations
//   return pumpingstations[0]
// }


/**
 * Get a pumping station info by its id
 */
export function getPumpingStation(id  : string): PumpingStation | null {

  const body = `
    PumpingStation.id
    PumpingStation.name
    PumpingStation.geoloc 
    PumpingStation.flow_rate
    PumpingStation.projects
    PumpingStation.energyprofiles
  `
  return getEntityById<PumpingStation>(DGRAPH_CONNECTION, "PumpingStation.id", id, body)
}
/**
 * Delete a pumping station by its id
 */

export function deletePumpingStation(id: string): void {
  deleteNodePredicates(DGRAPH_CONNECTION, `eq(PumpingStation.id, "${id}")`, [
    "PumpingStation.id",
    "PumpingStation.name",
    "PumpingStation.geoloc",
    "PumpingStation.flow_rate",
    "PumpingStation.projects",
    "PumpingStation.energyprofiles",
  ])
}


/**
 * Search products by similarity to a given text
 */
export function searchPumpingStations(search: string): PumpingStation[] {
  const embedding = embedText([search])[0]
  const topK = 3
  const body = `
    PumpingStation.id
    PumpingStation.name
    PumpingStation.geoloc
    PumpingStation.flow_rate
    PumpingStation.projects 
    PumpingStation.energyprofiles 
    `
  return searchBySimilarity<PumpingStation>(DGRAPH_CONNECTION, embedding, "PumpingStation.embedding", body, topK)
}

export function getEnergyProfile(id  : string): EnergyProfile | null {

  const body = `
    EnergyProfile.id
    EnergyProfile.name
    EnergyProfile.day 
    EnergyProfile.mont
    EnergyProfile.price
    EnergyProfile.pumpingstation_id
  `
  return getEntityById<EnergyProfile>(DGRAPH_CONNECTION, "EnergyProfile.id", id, body)
}