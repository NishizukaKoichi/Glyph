import type { GlyphToken, WebAuthnRegistrationOptions, WebAuthnAuthenticationOptions } from '../types/auth'

const API_BASE = '/auth'

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new ApiError(
      data.detail || `HTTP ${response.status}`,
      response.status,
      data
    )
  }

  return response.json()
}

// OAuth APIs
export const oauth = {
  login: (provider: 'google' | 'microsoft' | 'github' | 'twitter') => {
    window.location.href = `${API_BASE}/login/${provider}`
  },
}

// WebAuthn APIs
export const webauthn = {
  registerStart: async (email: string): Promise<WebAuthnRegistrationOptions> => {
    return fetchApi('/webauthn/register/start', {
      method: 'POST',
      body: JSON.stringify({ email }),
    })
  },

  registerFinish: async (email: string, credential: any): Promise<GlyphToken> => {
    return fetchApi('/webauthn/register/finish', {
      method: 'POST',
      body: JSON.stringify({ email, credential }),
    })
  },

  authenticateStart: async (email: string): Promise<WebAuthnAuthenticationOptions> => {
    return fetchApi('/webauthn/authenticate/start', {
      method: 'POST',
      body: JSON.stringify({ email }),
    })
  },

  authenticateFinish: async (email: string, credential: any): Promise<GlyphToken> => {
    return fetchApi('/webauthn/authenticate/finish', {
      method: 'POST',
      body: JSON.stringify({ email, credential }),
    })
  },
}
