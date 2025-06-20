from spatialgrid import SpatialGrid

class MessageBus:
    def __init__(self, agent_entities, config=None):
        self.global_config = config or {}
        self.comm_range = self.global_config.get("comm_range", 0.1)
        self.msg_type = self.global_config.get("type", "broadcast")
        self.kind = self.global_config.get("kind", "anonymous")
        self.enable = self.global_config.get("enable", False)
        self.grid = SpatialGrid(self.comm_range)
        self.mailboxes = {agent.get_name(): [] for agent in agent_entities}

    def update_grid(self,agents):
        self.grid.clear()
        for agent in agents:
            self.grid.insert(agent)

    def reset_mailboxes(self):
        for k in self.mailboxes:
            self.mailboxes[k] = []

    def send_message(self, sender, message):
        if not self.enable:
            return
        neighbors = self.grid.neighbors(sender, self.comm_range)
        msg = message
        if self.msg_type == "broadcast":
            for agent in neighbors:
                msg.update({"from": sender.get_name() if self.kind == "id" else None})
                self.mailboxes[agent.get_name()].append(msg)
        elif self.msg_type == "hand_shake":
            receiver_id = message.get("to")
            for agent in neighbors:
                if agent.get_name() == receiver_id:
                    msg.update({"from": sender.get_name() if self.kind == "id" else None})
                    self.mailboxes[agent.get_name()].append(msg)
        elif self.msg_type == "rebroadcast":
            for agent in neighbors:
                msg.update({"from": sender.get_name() if self.kind == "id" else None})
                self.mailboxes[agent.get_name()].append(msg)

    def receive_messages(self, receiver):
        messages = self.mailboxes[receiver.get_name()][:]
        self.mailboxes[receiver.get_name()] = []
        return messages
    
    def close(self):
        self.grid.close()
        del self.mailboxes,self.grid
        return