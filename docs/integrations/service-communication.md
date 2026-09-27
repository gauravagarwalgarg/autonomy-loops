---
title: Service Communication
description: gRPC, Protobuf, REST, and GraphQL patterns for agent-to-service communication
tags:
  - grpc
  - protobuf
  - rest
  - graphql
  - json
---

# Service Communication

AutonomyLoops agents communicate with external services and other agents using industry-standard protocols. This guide covers patterns for gRPC, Protobuf, REST, and GraphQL.

## Protocol Selection

| Protocol | Best For | Latency | Streaming | Schema | Agent Use Case |
|---|---|---|---|---|---|
| **gRPC** | Internal services, high-throughput | Very Low | Bidirectional | Protobuf | Agent-to-agent, tool backends |
| **REST/JSON** | Public APIs, CRUD | Low | SSE only | OpenAPI | External integrations, LLM APIs |
| **GraphQL** | Flexible queries, frontend | Medium | Subscriptions | SDL | Knowledge retrieval, complex queries |
| **JSON-RPC** | Simple RPC, MCP | Low | WebSocket | JSON Schema | MCP tool servers |
| **WebSocket** | Real-time, streaming | Very Low | Full-duplex | Custom | Live agent output, HITL |

## gRPC & Protobuf

### Agent Service Definition

```protobuf
// proto/autonomy_loops/v1/agent.proto
syntax = "proto3";

package autonomy_loops.v1;

import "google/protobuf/timestamp.proto";
import "google/protobuf/struct.proto";

service AgentService {
  // Submit a task to an agent
  rpc RunTask(RunTaskRequest) returns (RunTaskResponse);
  
  // Stream agent execution progress
  rpc StreamTask(RunTaskRequest) returns (stream TaskProgress);
  
  // Request approval (HITL)
  rpc RequestApproval(ApprovalRequest) returns (ApprovalResponse);
  
  // Health check
  rpc Health(HealthRequest) returns (HealthResponse);
}

message RunTaskRequest {
  string task = 1;
  string role = 2;
  string mode = 3;
  string provider = 4;
  string model = 5;
  google.protobuf.Struct context = 6;
  int32 max_iterations = 7;
}

message RunTaskResponse {
  bool success = 1;
  string output = 2;
  int32 iterations = 3;
  int64 total_tokens = 4;
  double elapsed_seconds = 5;
  string state = 6;
}

message TaskProgress {
  string state = 1;
  int32 iteration = 2;
  string message = 3;
  google.protobuf.Timestamp timestamp = 4;
  oneof detail {
    LLMCall llm_call = 5;
    ToolCall tool_call = 6;
    PolicyEvent policy_event = 7;
  }
}

message LLMCall {
  string provider = 1;
  string model = 2;
  int64 prompt_tokens = 3;
  int64 completion_tokens = 4;
  double latency_ms = 5;
}

message ToolCall {
  string name = 1;
  string category = 2;
  bool success = 3;
  double latency_ms = 4;
}

message PolicyEvent {
  string rule = 1;
  string decision = 2;  // allow, deny, require_approval
  string message = 3;
}

message ApprovalRequest {
  string id = 1;
  string agent_id = 2;
  string action_type = 3;
  string description = 4;
  google.protobuf.Struct context = 5;
}

message ApprovalResponse {
  string status = 1;  // approved, rejected, timed_out
  string resolved_by = 2;
  string comment = 3;
}

message HealthRequest {}
message HealthResponse {
  string status = 1;
  string version = 2;
}
```

### gRPC Server Implementation

```python
import grpc
from concurrent import futures
from autonomy_loops import Agent, Config
from autonomy_loops._factory import create_provider
from proto import agent_pb2, agent_pb2_grpc

class AgentServicer(agent_pb2_grpc.AgentServiceServicer):
    """gRPC server for AutonomyLoops agents."""
    
    def __init__(self, config: Config):
        self.config = config
    
    async def RunTask(self, request, context):
        provider = create_provider(request.provider or "anthropic", self.config)
        agent = Agent(
            role=request.role,
            mode=request.mode,
            provider=provider,
            config=self.config,
        )
        result = await agent.run(request.task)
        return agent_pb2.RunTaskResponse(
            success=result.success,
            output=result.output,
            iterations=result.iterations,
            total_tokens=result.total_tokens,
            elapsed_seconds=result.elapsed_seconds,
            state=result.state.value,
        )
    
    async def StreamTask(self, request, context):
        """Stream agent progress as it executes."""
        # Implementation streams TaskProgress messages
        ...

def serve(port: int = 50051):
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    agent_pb2_grpc.add_AgentServiceServicer_to_server(
        AgentServicer(Config.load()), server
    )
    server.add_insecure_port(f"[::]:{port}")
    await server.start()
    await server.wait_for_termination()
```

### gRPC Client Usage

```python
import grpc
from proto import agent_pb2, agent_pb2_grpc

async def call_agent(task: str, role: str = "developer"):
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = agent_pb2_grpc.AgentServiceStub(channel)
        
        response = await stub.RunTask(agent_pb2.RunTaskRequest(
            task=task,
            role=role,
            mode="code",
        ))
        print(f"Success: {response.success}")
        print(f"Output: {response.output}")
```

## REST / JSON API

### OpenAPI Specification

```yaml
# openapi.yaml
openapi: 3.1.0
info:
  title: AutonomyLoops API
  version: 2.0.0

paths:
  /api/v1/agents/run:
    post:
      summary: Run an agent task
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required: [task]
              properties:
                task: {type: string}
                role: {type: string, default: developer}
                mode: {type: string, default: code}
                provider: {type: string}
                max_iterations: {type: integer, default: 50}
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AgentResult'

  /api/v1/pipelines/run:
    post:
      summary: Run a multi-agent pipeline
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required: [pipeline]
              properties:
                pipeline: {type: string}
                context: {type: object}

components:
  schemas:
    AgentResult:
      type: object
      properties:
        success: {type: boolean}
        output: {type: string}
        iterations: {type: integer}
        total_tokens: {type: integer}
        elapsed_seconds: {type: number}
        state: {type: string}
```

## JSON Serialization Best Practices

```python
from pydantic import BaseModel
from datetime import datetime

class AgentEvent(BaseModel):
    """Standard event envelope for agent communication."""
    event_type: str
    agent_id: str
    timestamp: datetime
    trace_id: str
    payload: dict
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }

# Produce consistent, parseable JSON
event = AgentEvent(
    event_type="task.completed",
    agent_id="agent-coder-01",
    timestamp=datetime.utcnow(),
    trace_id="abc123",
    payload={"iterations": 5, "tokens": 1200},
)
print(event.model_dump_json(indent=2))
```

## Protocol Buffers Best Practices

!!! tip "Protobuf Design Rules"

    1. **Never change field numbers** They are the wire format identity
    2. **Use `optional` for new fields** Maintains backward compatibility
    3. **Prefer `string` over `enum`** Easier to extend without breaking clients
    4. **Version your packages** `autonomy_loops.v1`, `autonomy_loops.v2`
    5. **Use `google.protobuf.Struct`** For dynamic/unstructured data
    6. **Keep messages small** Split large payloads into streaming chunks
    7. **Use `oneof` for variants** Type-safe discriminated unions
