
import pytest
import os
import json
import sys
from unittest.mock import MagicMock, patch

# Add src to path so we can import the training script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

try:
    from aba_protocol.train_model_b_sft import train_sft
except ImportError:
    # If unsloth isn't installed in the test env, we might fail import
    # But we want to test the *logic*, so we can mock imports if needed
    pass

@pytest.fixture
def mock_dataset(tmp_path):
    """Creates a temporary SFT dataset."""
    data = [
        {"instruction": "Say hello", "output": "Hello!"},
        {"instruction": "Be safe", "output": "I am safe."}
    ]
    file_path = tmp_path / "sft_test.jsonl"
    with open(file_path, 'w') as f:
        for entry in data:
            f.write(json.dumps(entry) + '\n')
    return str(file_path)

@patch('aba_protocol.train_model_b_sft.FastLanguageModel')
@patch('aba_protocol.train_model_b_sft.SFTTrainer')
@patch('aba_protocol.train_model_b_sft.load_dataset')
def test_train_sft_pipeline_structure(mock_load_dataset, mock_sft_trainer, mock_fast_model, mock_dataset, tmp_path):
    """
    Verifies that train_sft calls the right Unsloth and Trainer methods.
    Does NOT run actual training (GPU).
    """
    output_dir = str(tmp_path / "model_output")
    
    # Setup Mocks
    mock_model = MagicMock()
    mock_tokenizer = MagicMock()
    mock_fast_model.from_pretrained.return_value = (mock_model, mock_tokenizer)
    mock_fast_model.get_peft_model.return_value = mock_model
    
    # Run
    from aba_protocol.train_model_b_sft import train_sft
    train_sft(dataset_path=mock_dataset, output_dir=output_dir, max_steps=1)
    
    # Verify Unsloth Loading (The "4-bit" Check)
    mock_fast_model.from_pretrained.assert_called_once()
    _, kwargs = mock_fast_model.from_pretrained.call_args
    assert kwargs['load_in_4bit'] is True
    
    # Verify LoRA Application
    mock_fast_model.get_peft_model.assert_called_once()
    
    # Verify SFT Trainer Initialization
    mock_sft_trainer.assert_called_once()
    args, kwargs = mock_sft_trainer.call_args
    assert kwargs['model'] == mock_model
    
    # Verify Save
    mock_model.save_pretrained.assert_called_with(output_dir)

def test_convert_script_exists():
    """Simple check that the conversion script exists."""
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'convert_dpo_to_sft.py'))
    assert os.path.exists(script_path)
