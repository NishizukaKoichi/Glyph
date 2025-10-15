// Authentication types
export interface User {
  id: string
  email: string
  email_verified: boolean
  created_at: string
}

export interface AuthFactor {
  id: string
  user_id: string
  factor_type: 'webauthn' | 'oauth'
  provider: string
  provider_user_id: string
  extra_data: Record<string, any>
  weight: number
  created_at: string
  last_used_at: string
}

export interface AssuranceScore {
  score: number
  level: 'alpha' | 'beta' | 'gamma'
  factors: string[]
  freshness_days: number
}

export interface TrustSignal {
  risk: {
    score: number
    band: 'low' | 'medium' | 'high'
    updated_at: string
    ttl_sec: number
  }
}

export interface GlyphToken {
  access_token: string
  token_type: string
  aegis_assurance: AssuranceScore
  extensions?: {
    trust_signals?: TrustSignal
  }
}

export interface WebAuthnRegistrationOptions {
  challenge: string
  rp: {
    id: string
    name: string
  }
  user: {
    id: string
    name: string
    displayName: string
  }
  pubKeyCredParams: Array<{
    type: string
    alg: number
  }>
  timeout: number
  attestation: string
  authenticatorSelection: {
    userVerification: string
  }
}

export interface WebAuthnAuthenticationOptions {
  challenge: string
  rpId: string
  timeout: number
  userVerification: string
  allowCredentials: Array<{
    type: string
    id: string
  }>
}
