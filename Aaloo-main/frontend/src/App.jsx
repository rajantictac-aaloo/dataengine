import { useState } from 'react'
import Frontpage from './pages/Frontpage'
import {Routes , Route} from 'react-router-dom'
import GRestaurant from './pages/GRestaurant'
import GoogleRev from './pages/GoogleRev'
import ZomRes from './pages/ZomRes'
import ZomRevi from './pages/ZomRevi'
import Ars from './pages/Ars'
import Trendingfood from './pages/Trendingfood'

function App() {


  return (
    
    <>
      <Routes>
        <Route path="/" element={<Frontpage />} />
        <Route path="/googlerestaurants" element={<GRestaurant/>} />
        <Route path="/googlereviews" element={<GoogleRev />} />
        <Route path="/zomatorestaurants" element={<ZomRes />} /> 
        <Route path="/zomatoreviews" element={<ZomRevi />} />
        <Route path="/arsvariable" element={<Ars />} />
        <Route path="/trendingfood" element={<Trendingfood/>} />
      </Routes>
     </>
  )
}

export default App
