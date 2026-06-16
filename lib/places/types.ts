export interface PlaceResult {
  id: string
  name: string
  address: string
  city: string
  state: string
  postcode: string
  phone: string
  website: string
  domain: string
  maps_url: string
  category: string
  email?: string
}

export interface SearchRequestBody {
  query: string
  location: string
  limit?: number
  cities?: string[] | null
  state?: string
}
