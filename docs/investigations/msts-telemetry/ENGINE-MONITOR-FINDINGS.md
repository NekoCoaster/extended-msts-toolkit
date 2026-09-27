# Engine safety-monitor state

This closes part of the unnamed saved-engine-subobject discovery lead. It does not establish real safety intervention, warning audibility or all-AI behavior.

`map_monitor_definitions.py` checks69 selected native instruction/table/string ranges against disk/live PID33612. Native parser tokens40475/76/77/78 name AWSMonitor, VigilanceMonitor, EmergencyStopMonitor and OverspeedMonitor. The engine parser directs them to definition+B0C/B78/BE4/CBC. Parser dispatch uses61f0ae/61f096; selected destination code is retained frompass58. No inference from configuration names alone is used.

Initializer005f212d assembly maps runtime engine+4BA/4FA/53A/5BA to those respective definition blocks through0060f99b. A fifth runtime slot+57A links definition+C50; its semantic name remains unresolved. Do not confuse the fourth explicitly serialized helper slot(+57A) with overspeed(+5BA). SaveEngine's enclosing raw range includes the latter; absence from the four fixup-helper calls does not mean it is unsaved.

0060f99b sets state+0 from whether definition+68 is nonzero, clears+4/+8/+C and several later words, initializes+10/+14/+18 to float-1, and stores definition at+3C. Caller005f212d can overwrite+0 from controller-specific fields. Therefore+0 is retained as an enable word, not a universal validity predicate or proof that the device is actively enforcing a rule.

Reset helper0060f8b0 conditionally loads state+10/+14/+1C/+18 from definition+0/+4/+8/+C, clears+4/+8/+C, then dispatches a method and handles configured action branches. Helper006107a0 returns true only when state+4 and linked definition+20 are nonzero. The controller aggregation00585e59 uses state+0 and+4 before reading definition action words. These establish a raw action-state role for+4, not an independently measured brake/power intervention. Countdown units and each state transition still need their update producer; raw scalar bits are preserved without naming them elapsed seconds.

Pass259:3functions598instructions2396bytes;pass260:3functions89instructions283bytes;pass261:2functions611instructions2196bytes. All emitted ranges match disk/live. Pass261 includes the generic object-method dispatcher006107cb; its presence is not a semantic description of every dispatched action. Parser00610e9e is retained for later per-field label/unit mapping.

## Live applicability

`engine-monitor-state-01` uses query/read-only access at paused73894.7265625. All four engines are enumerated through guarded physical registry reads. Lead200223 has all five expected definition links. Enable words are1/1/1/0/0 for AWS/vigilance/emergency/unnamed/overspeed; all action words are0. Trailing player200224 and AI200146/200147 have null links in all five slots. They are unavailable, not evidence of zero safety enforcement elsewhere.

The capture retains64raw state bytes and108definition bytes for available slots, expected link validation, identity/state/config rereads and exact probe copies. It does not interpret every retained word. Null links are not dereferenced. Reads are sequential and do not prove atomicity, ABA safety or future lifecycle validity. Inspect individual stability flags rather than relying on the absence of exceptions.

Four structured candidates are added, one for each named monitor state, with raw enable/action words, remaining state and definition provenance. The unnamed fifth slot is retained as a discovery lead, not assigned an invented subsystem name. Inventory1034=433direct26derived68cab507config. No controls, assets, executable or production code changed. Next: trace monitor update/countdown producers and action labels, then observe controlled acknowledgement/intervention transitions if a suitable gameplay fixture is available.
