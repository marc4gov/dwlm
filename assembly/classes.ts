import { Point } from "@hypermode/modus-sdk-as/assembly/postgresql"
import { JSON } from "json-as"


@json
export class PriceProfile {
    @alias("PriceProfile.id")
    id!: string

    @alias("PriceProfile.pumpingstation")  
    pumpingstation: PumpingStation | null = null    // Actually store the ID as string

    @alias("PriceProfile.datestring")
    datestring: string = ""

    @alias("PriceProfile.price")
    price: f32[] = []
}

@json
export class PowerProfile {
    @alias("PowerProfile.id")
    id!: string

    @alias("PowerProfile.pumpingstation")  
    pumpingstation: PumpingStation | null = null    // Actually store the ID as string

    @alias("PowerProfile.datestring")
    datestring: string = ""

    @alias("PowerProfile.flowrate")
    price: f32[] = []
}

@json
export class PumpingStation {
    @alias("PumpingStation.id")
    id!: string

    @alias("PumpingStation.name")
    name: string = ""

    @alias("PumpingStation.priceprofiles") 
    priceprofiles: PriceProfile[] | null = null

    @alias("PumpingStation.powerprofiles") 
    powerprofiles: PowerProfile[] | null = null
}