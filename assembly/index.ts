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


import { Model, ModelInfo } from "@hypermode/modus-sdk-as/assembly/models"
import { JSON } from "json-as"


@json
class ModelResponse {
  actions: Array<f32> = []
}

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

class EnergyOptimizerModel extends Model<EnergyInput, EnergyOutput> {
  debug: boolean

  constructor(info: ModelInfo) {
    super(info)
    this.debug = true
  }

  invoke(input: EnergyInput): EnergyOutput {
    // Create output class
    const output = new EnergyOutput()

    // Log the input to verify data
    console.log("Model Input - Profiles: " + input.profiles.toString())
    console.log("Model Input - Prices: " + input.prices.toString())

    // Call the actual model endpoint and get response
    const response: EnergyOutput = super.invoke(input)
    
    // Log the response
    console.log("Model Response: " + JSON.stringify(response))

    // Copy the actions from response
    if (response && response.actions) {
      output.actions = response.actions
    } else {
      output.actions = new Array<f32>(24).fill(0)
    }

    return output
  }
}

export function optimizeEnergy(profiles: Array<f32>, prices: Array<f32>): Array<f32> {
  console.log("Function called with profiles length: " + profiles.length.toString())
  console.log("Function called with prices length: " + prices.length.toString())

  // Input validation
  if (profiles.length != 24 || prices.length != 24) {
    console.error("Invalid input: Profiles and prices must have length 24")
    return new Array<f32>(24).fill(0)  // non-fatal error with default return
  }

  if (!profiles || !prices) {
    throw new Error("Missing required input: profiles or prices")  // fatal error
  }

  // Get the model
  const model = models.getModel<EnergyOptimizerModel>("energy-optimizer")
  
  // Create input
  const input = new EnergyInput(profiles, prices)

  // Invoke model and get output
  const output = model.invoke(input)
  console.log("Model output actions: " + output.actions.toString())
  
  if (!output.actions || output.actions.length === 0) {
    console.error("Model returned no actions")
    return new Array<f32>(24).fill(0)  // non-fatal error with default return
  }

  return output.actions
}