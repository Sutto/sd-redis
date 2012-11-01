#!/usr/bin/env python

import subprocess

class Redis:
    def __init__(self, agent_config, checks_logger, raw_config):
        self.agent_config = agent_config
        self.checks_logger = checks_logger
        self.raw_config = raw_config

        self.command = ["redis-cli"]
        if 'Redis' in self.raw_config:
            config = self.raw_config['Redis']
            if 'password' in config:
                self.command.extend(('-a', config['host']))
        self.command.append("info")

    def run(self):
        try:
            output = subprocess.check_output(self.command)
            stats = dict((key.strip(), value.strip()) for (key, value) in (line.split(':', 1) for line in output.splitlines() if ':' in line))
            return stats
        except subprocess.CalledProcessError:
            self.checks_logger.exception("Redis doesn't seem to be running, perhaps check your configuration?")
            return {}

if __name__ == '__main__':
    import logging
    print Redis({}, logging, {}).run()
