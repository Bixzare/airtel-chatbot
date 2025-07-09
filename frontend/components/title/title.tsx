"use client";
import * as React from 'react';
import { AirtelLogo } from "./airtel-logo";


export default function TItle(){

    const [loading,setLoading] = React.useState(true);

    React.useEffect(() => {
        setLoading(false);
    },[]);

    return( 
        <div className ="flex w-auto flex-col items-center p-4 ">
            {
                loading ? 
                (<div  className ="flex justify-center items-center flex-col"><h1 className="text-2xl font-bold text-center mb-4"><div className ="w-60 h-40 bg-[#E31F26]/50 rounded-full animate-pulse"></div></h1>
            <p className="text-center !text-foreground">Your personal assistant for all Airtel services</p> 
      </div>) 
                :
                (<div className ="flex justify-center items-center flex-col"><h1 className="text-2xl font-bold text-center mb-4"><AirtelLogo/></h1>
            <p className="text-center text-foreground">Your personal assistant for all Airtel services</p> 
      </div>)
            }
              </div>
    )
}