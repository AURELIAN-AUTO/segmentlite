/**
 * SegmentLite TypeScript/JavaScript Client SDK.
 * Ultra-lightweight drop-in alternative for Segment analytics.
 */

export interface TrackOptions {
  userId?: string;
  anonymousId?: string;
  properties?: Record<string, any>;
  context?: Record<string, any>;
}

export interface IdentifyOptions {
  traits?: Record<string, any>;
  context?: Record<string, any>;
}

export interface DestinationOptions {
  name: string;
  url: string;
  type?: 'webhook' | 'slack' | 'http_relay';
  headers?: Record<string, string>;
  eventsFilter?: string[];
  enabled?: boolean;
}

export class SegmentLite {
  private apiKey: string;
  private host: string;

  constructor(options: { apiKey: string; host?: string }) {
    this.apiKey = options.apiKey;
    this.host = (options.host || 'https://segmentlite-api-dfru.fly.dev').replace(/\/$/, '');
  }

  async track(event: string, options: TrackOptions = {}) {
    return this.request('/v1/track', 'POST', {
      event,
      user_id: options.userId,
      anonymous_id: options.anonymousId,
      properties: options.properties || {},
      context: options.context || {}
    });
  }

  async identify(userId: string, options: IdentifyOptions = {}) {
    return this.request('/v1/identify', 'POST', {
      user_id: userId,
      traits: options.traits || {},
      context: options.context || {}
    });
  }

  async addDestination(options: DestinationOptions) {
    return this.request('/v1/destinations', 'POST', {
      name: options.name,
      type: options.type || 'webhook',
      url: options.url,
      headers: options.headers || {},
      events_filter: options.eventsFilter,
      enabled: options.enabled ?? true
    });
  }

  async getDestinations() {
    return this.request('/v1/destinations', 'GET');
  }

  async getStats() {
    return this.request('/v1/stats', 'GET');
  }

  private async request(endpoint: string, method: string, data?: any) {
    const res = await fetch(`${this.host}${endpoint}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': this.apiKey,
        'User-Agent': 'SegmentLite-TS/1.0.0'
      },
      body: data ? JSON.stringify(data) : undefined
    });

    if (!res.ok) {
      const err = await res.text();
      throw new Error(`SegmentLite API Error (${res.status}): ${err}`);
    }
    return res.json();
  }
}
