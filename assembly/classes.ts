@json
export class HourRate {
    // @alias("HourRate.id")
    id!: string

    // @alias("HourRate.xid")
    xid: string = ""

    // @alias("HourRate.h0")
    h0!: f32
    // @alias("HourRate.h1")
    h1!: f32
    // @alias("HourRate.h2")
    h2!: f32
    // @alias("HourRate.h3")
    h3!: f32
    // @alias("HourRate.h4")
    h4!: f32
    // @alias("HourRate.h5")
    h5!: f32
    // @alias("HourRate.h6")
    h6!: f32
    // @alias("HourRate.h7")
    h7!: f32
    // @alias("HourRate.h8")
    h8!: f32
    // @alias("HourRate.h9")
    h9!: f32
    // @alias("HourRate.h10")
    h10!: f32
    // @alias("HourRate.h11")
    h11!: f32
    // @alias("HourRate.h12")
    h12!: f32
    // @alias("HourRate.h13")
    h13!: f32
    // @alias("HourRate.h14")
    h14!: f32
    // @alias("HourRate.h15")
    h15!: f32
    // @alias("HourRate.h16")
    h16!: f32
    // @alias("HourRate.h17")
    h17!: f32
    // @alias("HourRate.h18")
    h18!: f32
    // @alias("HourRate.h19")
    h19!: f32
    // @alias("HourRate.h20")
    h20!: f32
    // @alias("HourRate.h21")
    h21!: f32
    // @alias("HourRate.h22")
    h22!: f32
    // @alias("HourRate.h23")
    h23!: f32
}

@json
export class Profile {
    // @alias("Profile.id")
    id!: string

    // @alias("Profile.xid")
    xid: string = ''

    // @alias("Profile.flow_per_hour")  
    flow_per_hour: HourRate | null = null  

    // @alias("Profile.price_per_hour")  
    price_per_hour: HourRate | null = null  

    // @alias("Profile.action_per_hour")  
    action_per_hour: HourRate | null = null  
}

@json
export class PumpingStation {
    // @alias("PumpingStation.id")
    id!: string

    // @alias("PumpingStation.xid")
    xid: string = ""

    // @alias("PumpingStation.name")
    name: string = ""

    // @alias("PumpingStation.profiles")
    // @omitnull()
    profiles: Profile[] | null = null

}