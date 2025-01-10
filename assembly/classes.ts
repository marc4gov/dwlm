import { Point } from "@hypermode/modus-sdk-as/assembly/postgresql"
import { Float } from "assemblyscript-json/assembly/JSON"
import { JSON } from "json-as"


@json
export class HourRate {
    @alias("HourRate.id")
    id!: string

    @alias("HourRate.hours")
    hours!: Float64Array
}

@json
export class Profile {
    @alias("Profile.id")
    id!: string

    @alias("Profile.xid")
    xid: String = ''

    @alias("Profile.flow_per_hour")  
    flow_per_hour: HourRate | null = null  

    @alias("Profile.price_per_hour")  
    price_per_hour: HourRate | null = null  

    @alias("Profile.action_per_hour")  
    action_per_hour: HourRate | null = null  
}

@json
export class PumpingStation {
    @alias("PumpingStation.id")
    id!: string

    @alias("PumpingStation.name")
    name: string = ""

    @alias("PumpingStation.profiles") 
    profiles: Profile[] | null = null

}