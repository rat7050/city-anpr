# API Documentation

## Authentication
`POST /api/v1/auth/token`
Returns JWT token.

## Cameras
`GET /api/v1/cameras`
`POST /api/v1/cameras`

## Vehicles
`GET /api/v1/vehicles/search`
`GET /api/v1/vehicles/{plate_number}`

## WebSockets
`WS /ws/live`
Receives live detection events.

## Error Codes
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
