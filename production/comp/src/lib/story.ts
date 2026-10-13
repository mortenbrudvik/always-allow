// The Agent's own session in the story, for the chrome's clock and counters, s110's racing counters and the end card.
// None of this production's real numbers is on screen (the owner's call on the rough cut, 30 Sep; the receipt went the
// same way). The clock runs with the song from 00:00:00. The counters stay at zero until the Human's one sentence
// lands on the drop, then climb, racing by the click, to 2^20 tool calls and 2^32 tokens: the same powers of two as
// s068's 4,096 tabs and 65,536 instances. Pure functions of song time.
import {clamp} from './ease';
import {barTime} from './time';

/** The drop: the sentence is sent, and the Agent starts. */
export const GOAL_AT = barTime(0);
/** Where the chrome switches off for the tail, and the counters stop. */
export const STOP_AT = barTime(145);
export const TOOL_CALLS = 2 ** 20;
export const TOKENS = 2 ** 32;

/** The share of the Agent's work done by song time t: none before the goal, then slow, then racing. */
export const work = (t: number) => Math.pow(clamp((t - GOAL_AT) / (STOP_AT - GOAL_AT)), 2.6);
