#!/usr/bin/env python

import subprocess

class Redis:

    subcommands = ['commandstats', 'cpu', 'stats', 'memory', 'persistence', 'server', 'clients']

    config_args = {
        "host": "-h",
        "port": "-p",
        "socket": "-s",
        "password": "-a"
    }

    def __init__(self, agent_config, checks_logger, raw_config):
        self.agent_config = agent_config
        self.checks_logger = checks_logger
        self.raw_config = raw_config

        self.command = ["redis-cli"]
        if 'Redis' in self.raw_config:
            config = self.raw_config['Redis']
            for (key, arg) in self.config_args.iteritems():
                if key in config:
                    self.command.extend((arg, config[key]))

    def run(self):
        try:
            stats = {}
            for subcommand in self.subcommands:
                output = subprocess.check_output(self.command + ["info", subcommand])
                for line in output.splitlines():
                    self.expand_result(stats, line)
            max_memory = subprocess.check_output(self.command + ["config", "get", "maxmemory"]).splitlines()[1].strip()
            if max_memory != '0':
                stats['memory_under_limit'] = str(int(max_memory) - int(stats['used_memory']))
            stats['running'] = True
            return stats
        except subprocess.CalledProcessError:
            self.checks_logger.exception("Redis doesn't seem to be running, perhaps check your configuration?")
            return {'running': False}
        except OSError:
            self.checks_logger.exception("redis-cli could not be found.")
            return {'running': False}

    def expand_result(self, onto, line):
        if ':' in line:
            key, value = line.split(":", 1)
            if "," in value and "=" in value:
                for choice in value.split(","):
                    child_key, child_value = choice.split("=", 1)
                    onto[key + "/" + child_key.strip()] = child_value.strip()
            else:
                onto[key] = value

if __name__ == '__main__':
    import logging
    print Redis({}, logging, {}).run()
