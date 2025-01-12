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
import { PumpingStation } from "./classes"
import { embedText } from "./embeddings"
import { buildPumpingStationMutationJson } from "./pumpingstation-helpers"
import {
  deleteNodePredicates,
  ListOf,
  searchBySimilarity,
  getEntityById,
  addEmbeddingToJson,
} from "./dgraph-utils"
import { JSON } from "json-as"



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


// Dgraph returns an array of objects
@json
class GetPumpingStationResponse {
  station: Array<PumpingStation> = []
}

export function getPumpingStation(xid: string): PumpingStation | null {
    const statement = `
    query pumpingStation($xid: string!) {
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
/**
 * Get a pumping station info by its id
 */
export function getPumpingStationAlias(id  : string): PumpingStation | null {

  const body = `
    PumpingStation.id
    PumpingStation.xid
    PumpingStation.name
    PumpingStation.profiles
  `
  return getEntityById<PumpingStation>(DGRAPH_CONNECTION, "PumpingStation.id", id, body)
}
/**
 * Delete a pumping station by its id
 */




/**
 * Search products by similarity to a given text
 */
export function searchPumpingStations(search: string): PumpingStation[] {
  const embedding = embedText([search])[0]
  const topK = 3
  const body = `
    PumpingStation.id
    PumpingStation.name
    `
  return searchBySimilarity<PumpingStation>(DGRAPH_CONNECTION, embedding, "PumpingStation.embedding", body, topK)
}


// import { Model, ModelInfo } from "@hypermode/modus-sdk-as/assembly/models"


// @json
// class ModelResponse {
//   actions: Array<f32> = []
// }

// @json
// class EnergyInput {
//   profiles: Array<f32>
//   prices: Array<f32>

//   constructor(profiles: Array<f32>, prices: Array<f32>) {
//     this.profiles = profiles
//     this.prices = prices
//   }
// }

// @json
// class EnergyOutput {
//   actions: Array<f32> = []
// }

// @json
// class EnergyOptimizerModel extends Model<EnergyInput, EnergyOutput> {

//   constructor(info: ModelInfo) {
//     super(info)
//   }

//   invoke(input: EnergyInput): EnergyOutput {
//     const result = super.invoke(input)

//     // Create a new EnergyOutput instance and copy the data
//     const output = new EnergyOutput()
//     output.actions = result.actions
//     return output
//   }
// }


// export function optimizeEnergy(profiles: Array<f32>, prices: Array<f32>): Array<f32> {
//   console.log("Function called with profiles length: " + profiles.length.toString())
//   console.log("Function called with prices length: " + prices.length.toString())

//   // Input validation
//   if (profiles.length != 24 || prices.length != 24) {
//     console.error("Invalid input: Profiles and prices must have length 24")
//     return new Array<f32>(24).fill(0)
//   }

//   if (!profiles || !prices) {
//     throw new Error("Missing required input: profiles or prices")
//   }

//   // Get the model
//   const model = models.getModel<EnergyOptimizerModel>("energy-optimizer")
  
//   // Create input
//   const input = new EnergyInput(profiles, prices)

//   // Invoke model and get output
//   const output = model.invoke(input)
//   const actions = changetype<EnergyOutput>(output).actions
//   console.log("Model output actions: " + actions.toString())
  
//   if (!actions || actions.length === 0) {
//     console.error("Model returned no actions")
//     return new Array<f32>(24).fill(0)
//   }

//   return actions  // Return the actions array directly
// }

import { http } from "@hypermode/modus-sdk-as"

@json 
class EnergyInput {
  profiles: Array<f32>
  prices: Array<f32>

  constructor(profiles: Array<f32>, prices: Array<f32>) {
    this.profiles = profiles
    this.prices = prices
  }
}

@json
class EnergyOutput {
  actions: Array<f32> = []
}

export function optimizeEnergy(profiles: Array<f32>, prices: Array<f32>): Array<f32> {
  // Input validation
  if (profiles.length != 24 || prices.length != 24) {
    throw new Error("Invalid input: Profiles and prices must have length 24")
  }

  const input = new EnergyInput(profiles, prices)
  const headers = http.Headers.from([
    ["Content-Type", "application/json"]
  ])
  
  const options = new http.RequestOptions()
  options.method = "POST"
  options.headers = headers
  options.body = http.Content.from(JSON.stringify(input))

  const response = http.fetch(
    "http://marc4gov.pythonanywhere.com/predict",
    options
  )
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  const output = response.json<EnergyOutput>()
  return output.actions
}