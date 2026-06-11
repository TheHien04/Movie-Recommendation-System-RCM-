import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { Navbar } from './components/Navbar'
import { Footer } from './components/Footer'
import { ToastHost } from './components/Toast'
import { OnboardingTour } from './components/OnboardingTour'
import { I18nProvider } from './lib/i18n'
import { Home } from './pages/Home'
import { Genres } from './pages/Genres'
import { Chat } from './pages/Chat'
import { MLStudio } from './pages/MLStudio'
import { Watchlist } from './pages/Watchlist'
import { Search } from './pages/Search'
import { MovieDetail } from './pages/MovieDetail'
import { Profile } from './pages/Profile'
import { Developers } from './pages/Developers'
import { Moods } from './pages/Moods'
import { Compare } from './pages/Compare'
import { Leaderboard } from './pages/Leaderboard'
import { MLBattle } from './pages/MLBattle'
import { Admin } from './pages/Admin'

export default function App() {
  return (
    <I18nProvider>
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/search" element={<Search />} />
        <Route path="/genres" element={<Genres />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/watchlist" element={<Watchlist />} />
        <Route path="/movie/:title" element={<MovieDetail />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/developers" element={<Developers />} />
        <Route path="/ml" element={<MLStudio />} />
        <Route path="/moods" element={<Moods />} />
        <Route path="/compare" element={<Compare />} />
        <Route path="/leaderboard" element={<Leaderboard />} />
        <Route path="/ml-battle" element={<MLBattle />} />
        <Route path="/admin" element={<Admin />} />
      </Routes>
      <Footer />
      <ToastHost />
      <OnboardingTour />
    </BrowserRouter>
    </I18nProvider>
  )
}
